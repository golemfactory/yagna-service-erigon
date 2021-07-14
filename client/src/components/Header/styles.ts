import styled, { css } from 'styled-components';
import { Col, Container } from 'react-grid-system';
import color from 'styles/colors';
import zIndex from 'styles/zIndexes';
import { FixedContainerMixin } from 'styles/mixins';
import metamaskLogo from 'assets/logo/metamask_logo.svg';
import HyperLink from '../HyperLink';

const MetamaskButtonMixin = (width: number) => css`
  width: ${width}rem;
  height: 5rem;

  display: flex;
  justify-content: center;
  align-items: center;

  color: ${color.blue};
  font-family: 'Inter Regular', sans-serif;
  font-size: 1.1rem;
  line-height: 1.4rem;
  text-transform: uppercase;
  letter-spacing: 0.4rem;

  background-color: transparent;
  background-image: url(${metamaskLogo});
  background-repeat: no-repeat;
  background-position: 3.5rem center;
  border: 0.1rem solid ${color.blue};
  border-radius: 2.6rem;

  padding-left: 3.5rem;
`;

export const StyledHeader = styled.div`
  width: 100%;
  height: 12rem;

  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: ${zIndex.Header};

  background-color: ${color.ash};

  button {
  }
`;

export const StyledContainer = styled(Container)`
  ${FixedContainerMixin};
`;

export const StyledCol = styled(Col)`
  height: 12rem;

  display: flex;
  align-items: center;
`;

export const StyledHyperlink = styled(HyperLink)`
  ${MetamaskButtonMixin(33)};
`;

export const StyledButton = styled.button`
  ${MetamaskButtonMixin(37)};
`;

export const StyledPlaceholder = styled.div`
  ${MetamaskButtonMixin(30)};

  position: relative;

  color: ${color.green};
  border-color: transparent;

  :before {
    content: '';

    width: 1.2rem;
    height: 1.2rem;

    position: absolute;
    top: 1.8rem;
    left: 9.2rem;

    background-color: ${color.green};
    border-radius: 50%;
  }
`;
