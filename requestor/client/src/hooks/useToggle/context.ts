import { createContext } from 'react';

const toggleContext = createContext({
  toggleOpen: false,
  toggleRef: undefined,
  toggleClick: () => {},
});

export default toggleContext;
