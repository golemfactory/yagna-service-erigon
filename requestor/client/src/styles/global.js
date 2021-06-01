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
    
    p {
      font-size: 1.6rem;
    }
    
    button {
      font-size: 1.6rem;
      
      margin: 2rem;
    }
    
    div {
      > span {
        font-size: 1.4rem;
        margin-right: 1rem;
      }
      
      a {
       margin-right: 1rem;
     }
    }
  }
`;

export default GlobalStyle;
