import { ToastContainer } from 'react-toastify';
import { Footer, Header, notify, Toast } from 'components';
import { DashboardPage, ProductPage } from 'pages';
import { useMetamask } from './hooks';
import GlobalStyle from 'styles/global';
import 'fonts/font-face.css';

const App = () => {
  const { active, metamask } = useMetamask();

  const handleNotify = () => notify(<Toast code={-32002} />);

  return (
    <>
      <GlobalStyle />
      <Header metamask={metamask} active={active} onNotify={handleNotify} />
      <ToastContainer hideProgressBar />
      {active ? <DashboardPage /> : <ProductPage onNotify={handleNotify} />}
      <Footer />
    </>
  );
};

export default App;
