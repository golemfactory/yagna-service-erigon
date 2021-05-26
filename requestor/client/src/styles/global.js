import { createGlobalStyle } from 'styled-components';
import styledNormalize from 'styled-normalize';

const GlobalStyle = createGlobalStyle`
  ${styledNormalize};

  * {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
    outline: none;
  }

  html {
    font-size: 10px;
  }
  
  body {
    background-color: #dfdfdf;
    padding: 2rem;
    
    h1 {
      font-size: 2rem;
    }
    
    p {
      font-size: 1.6rem;
    }
  }
`;

export default GlobalStyle;
