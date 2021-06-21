import styled from 'styled-components';
import { Tabs } from 'react-tabs';
import color from 'styles/colors';

export const StyledTabs = styled(Tabs)`
  .react-tabs {
    -webkit-tap-highlight-color: transparent;
  }

  .react-tabs__tab-list {
    border: 0.1rem solid transparent;
    border-bottom-color: ${color.petrol};

    margin: 9rem 0 4rem;
    padding: 0;
  }

  .react-tabs__tab {
    width: 20rem;

    display: inline-block;
    list-style: none;

    text-align: center;

    padding: 1.6rem 1rem;

    cursor: pointer;
  }

  .react-tabs__tab--selected {
    background-color: ${color.ash};
    border-radius: 0;
  }

  .react-tabs__tab--disabled {
    color: ${color.grey};

    cursor: default;
  }

  .react-tabs__tab:focus {
    box-shadow: none;
  }

  .react-tabs__tab-panel {
    display: none;
  }

  .react-tabs__tab-panel--selected {
    display: block;
  }
`;
