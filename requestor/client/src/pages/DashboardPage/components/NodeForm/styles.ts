import styled, { css } from 'styled-components';
import { Col } from 'react-grid-system';
import color from 'styles/colors';
import addOpacityToColor from 'utils/addOpacityToColor';
import checkmark from 'assets/icons/checkmark.svg';

export const StyledForm = styled.form`
  border: 0.1rem solid ${color.ash};
  box-shadow: 0 0.2rem 0.6rem 0 ${addOpacityToColor(color.black, 10)};
  border-radius: 1.4rem;

  margin: 18rem 0 4rem;
  padding: 6rem 4rem 0;
`;

export const StyledCol = styled(Col)<{ fieldset?: boolean }>`
  display: flex;
  flex-direction: column;

  padding-bottom: 6rem;

  > label {
    font-family: 'Inter Bold', sans-serif;
  }

  button {
    :first-of-type {
      margin-top: 8rem;
    }

    :last-of-type {
      margin-top: 2rem;
    }
  }
`;

export const StyledField = styled.fieldset<{ error: boolean }>`
  display: flex;
  flex-direction: column;

  border: none;

  padding: 0;

  label {
    font-family: 'Inter Bold', sans-serif;

    margin-bottom: 3rem;
  }

  input {
    width: 27rem;
    height: 5rem;

    color: ${color.navy};
    font-size: 0.9rem;
    line-height: 1.1rem;

    background-color: ${color.ash};
    border: none;
    border-bottom: 0.2rem solid ${({ error }) => (error ? color.red : color.petrol)};
    border-radius: 0.4rem 0.4rem 0 0;

    padding: 0 1.6rem;
  }

  span {
    color: ${color.red};
    font-size: 0.9rem;
    line-height: 1.1rem;

    margin-top: 2.4rem;
  }
`;

export const StyledNetworks = styled.div`
  display: flex;
  flex-wrap: wrap;
`;

export const StyledRadioField = styled.fieldset<{ checked: boolean; disabled?: boolean }>`
  position: relative;

  border: none;

  padding: 0;
  margin-top: 3rem;

  width: 35%;

  :first-of-type {
    width: 100%;
  }

  :before {
    content: '';

    width: 1.2rem;
    height: 1.2rem;

    position: absolute;
    top: 0.3rem;
    left: 0;

    border: 0.1rem solid ${({ disabled }) => (disabled ? color.grey : color.petrol)};
    border-radius: 50%;
  }

  :after {
    content: '';

    width: 1.2rem;
    height: 1.2rem;

    position: absolute;
    top: 0.3rem;
    left: 0;

    border: 0.1rem solid transparent;
    background-color: ${({ checked }) => (checked ? color.petrol : 'transparent')};
    background-image: url(${checkmark});
    background-repeat: no-repeat;
    background-position: center;
    border-radius: 50%;
  }

  label {
    font-size: 1.4rem;
    line-height: 1.9rem;

    padding-left: 2.7rem;
  }

  ${({ disabled }) =>
    disabled &&
    css`
      color: ${color.grey};
    `}
`;
