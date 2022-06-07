import { useEffect, useState } from 'react';
import { useWeb3React } from '@web3-react/core';
import { InjectedConnector } from '@web3-react/injected-connector';
import detectEthereumProvider from '@metamask/detect-provider';
import { isNull } from 'lodash';
import { AUTH_INIT, AUTH_PENDING, AuthTicket } from '../../utils/httpRequest/httpRequest';
import { auth } from '../../utils/auth';

const injected = new InjectedConnector({
  supportedChainIds: [1, 3, 42, 4, 5, 137],
});

export const useMetamask = (): {
  account: string | null | undefined;
  active: boolean;
  metamask: any;
  authTicket: AuthTicket;
} => {
  const { account, active, activate, library } = useWeb3React();
  const [metamask, setMetamask] = useState(library && library.givenProvider.isMetaMask);

  useEffect(() => {
    detectEthereumProvider().then(
      (result: any) =>
        !isNull(result) &&
        (result !== window.ethereum ? console.log('Multiple wallets') : setMetamask(result.isMetaMask)),
    );
  }, []);

  useEffect(() => {
    activate(injected);
  }, [activate]);

  useEffect(() => {
    setMetamask(library && library.givenProvider.isMetaMask);
  }, [library]);

  const [authTicket, setAuthTicket] = useState(AUTH_INIT);
  useEffect(() => {
    if (active && library && library.givenProvider.isMetaMask) {
      if (
        typeof account === 'string' &&
        (authTicket.status === 'init' || (authTicket.status === 'authorized' && authTicket.account != account))
      ) {
        setAuthTicket(AUTH_PENDING);
        auth(account, async (message) => {
          const response = await library.eth.personal.sign(library.utils.toHex(message), account);
          return response;
        })
          .then(({ message, response }) =>
            setAuthTicket({ status: 'authorized', challenge: message, response, account: account! }),
          )
          .catch((error) => setAuthTicket({ status: 'error', error }));
      }
    }
  }, [library, active, account]);

  // @ts-ignore
  const cypress = window.Cypress;

  return {
    account: !cypress ? account : '0x25bb4351B805884663d278F10A2096437Ee29855',
    active: !cypress ? active : true,
    metamask,
    authTicket,
  };
};
