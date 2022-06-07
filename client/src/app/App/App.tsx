import { ToastContainer } from 'react-toastify';
import { Footer, Header, notify, Toast } from 'components';
import { DashboardPage, ProductPage } from 'pages';
import { useMetamask } from './hooks';
import GlobalStyle from 'styles/global';
import 'fonts/font-face.css';

const App = () => {
  const { active, metamask, authTicket } = useMetamask();

  const handleNotify = () => notify(<Toast code={-32002} />);

  return (
    <>
      <GlobalStyle />
      <Header metamask={metamask} active={active && authTicket.status !== 'init'} onNotify={handleNotify} />
      <ToastContainer hideProgressBar />
      {active && authTicket.status !== 'init' ? <DashboardPage /> : <ProductPage onNotify={handleNotify} />}
      <Footer />
    </>
  );
};

export default App;
