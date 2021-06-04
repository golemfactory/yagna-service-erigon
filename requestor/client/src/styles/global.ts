import { createGlobalStyle } from 'styled-components';
import styledNormalize from 'styled-normalize';
import 'react-toastify/dist/ReactToastify.css';
import color from './colors';

const GlobalStyle = createGlobalStyle`
  ${styledNormalize};

  * {
    box-sizing: border-box;
    -webkit-tap-highlight-color: transparent;
    outline: none;
  }

  ::selection {
    color: ${color.white};
    
    background-color: ${color.navy};
  }

  html {
    font-size: 10px;
  }

  body {
    min-height: 100vh;
    
    position: relative;
    
    color: ${color.navy};
    font-family: 'Roboto Mono Medium', monospace;
    font-size: 0.8rem;
    line-height: 1.1rem;
  }

  .Toastify {
    .Toastify__toast-container--top-right {
      top: 15rem;
    }

    .Toastify__toast {
      font-family: 'Inter Medium', sans-serif ;
      color: ${color.navy};

      background-color: ${color.white};
      border: 0.1rem solid;
    }

    .Toastify__toast--error {
      border-color: ${color.red};

      svg {
        fill: ${color.red};
      }
    }

    .Toastify__toast--success {
      border-color: ${color.green};
      
      svg {
        fill: ${color.green};
      }
    }
    
    .Toastify__toast-body {
      width: 100%;
    }
  }
`;

export default GlobalStyle;
