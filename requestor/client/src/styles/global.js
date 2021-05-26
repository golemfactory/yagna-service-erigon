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
  }
`;

export default GlobalStyle;
