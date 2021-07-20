import { useEffect, useState } from 'react';
import { useWeb3React } from '@web3-react/core';
import { InjectedConnector } from '@web3-react/injected-connector';
import detectEthereumProvider from '@metamask/detect-provider';
import { isNull } from 'lodash';

const injected = new InjectedConnector({
  supportedChainIds: [1, 3, 42, 4, 5],
});

export const useMetamask = () => {
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

  // @ts-ignore
  const cypress = window.Cypress;

  return {
    account: !cypress ? account : '0x25bb4351B805884663d278F10A2096437Ee29855',
    active: !cypress ? active : true,
    metamask,
  };
};
