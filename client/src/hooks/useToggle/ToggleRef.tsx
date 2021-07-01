import React, { forwardRef, LegacyRef, ReactNode, useContext } from 'react';
import { toggleContext } from './index';

const ToggleRef = forwardRef(({ children, ...props }: { children: ReactNode }, ref: LegacyRef<any>) => {
  const { toggleRef } = useContext(toggleContext);

  return (
    <div
      style={{ position: 'relative' }}
      // @ts-ignore
      ref={toggleRef || ref}
      {...props}
    >
      {children}
    </div>
  );
});

export default ToggleRef;
