import { useEffect, useState } from 'react';
import { useWeb3React } from '@web3-react/core';
import { InjectedConnector } from '@web3-react/injected-connector';
import detectEthereumProvider from '@metamask/detect-provider';
import { isNull } from 'lodash';
import { Header } from '../../components';
import { DashboardPage, ProductPage } from '../../pages';
import GlobalStyle from '../../styles/global';

const injected = new InjectedConnector({
  supportedChainIds: [1, 3, 42, 4, 5],
});

const App = () => {
  const { activate, active, library } = useWeb3React();

  const [metamask, setMetamask] = useState(library && library.givenProvider.isMetaMask);

  useEffect(() => {
    detectEthereumProvider().then(
      (result) =>
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

  return (
    <>
      <GlobalStyle />
      <Header metamask={metamask} />
      {active ? <DashboardPage /> : <ProductPage />}
    </>
  );
};

export default App;
