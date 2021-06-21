import styled, { css } from 'styled-components';
import color from 'styles/colors';

export const StyledButton = styled.button<{ outlined?: boolean; ghost?: boolean }>`
  width: 29.5rem;
  height: 5rem;

  color: ${color.white};
  font-family: 'Inter Regular', sans-serif;
  font-size: 1.1rem;
  line-height: 1.4rem;
  text-transform: uppercase;
  letter-spacing: 0.4rem;

  background-color: ${color.petrol};
  border: 0.1rem solid ${color.petrol};

  margin: 0;

  :hover {
    color: ${color.petrol};

    background-color: ${color.white};
  }

  ${({ outlined }) =>
    outlined &&
    css`
      color: ${color.petrol};

      background-color: ${color.white};

      :hover {
        color: ${color.white};

        background-color: ${color.petrol};
      }
    `}

  ${({ ghost }) =>
    ghost &&
    css`
      color: ${color.petrol};

      background-color: ${color.white};
      border-color: transparent;

      :hover {
        border-color: ${color.petrol};
      }
    `}
`;
