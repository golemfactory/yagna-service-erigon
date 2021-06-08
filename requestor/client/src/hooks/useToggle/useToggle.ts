import { createRef, useEffect, useState } from 'react';
import { ToggleProps, useToggleProps } from './types';

const useToggle = ({ open = false }: useToggleProps): ToggleProps => {
  const [toggleOpen, setToggleOpen] = useState(open);

  useEffect(() => {
    setToggleOpen(open);
  }, [open]);

  const toggleRef = createRef();

  const toggleClick = () => setToggleOpen(!toggleOpen);

  return { toggleOpen, toggleRef, toggleClick };
};

export default useToggle;
