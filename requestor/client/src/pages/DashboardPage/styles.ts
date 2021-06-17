import styled from 'styled-components';
import { Col } from 'react-grid-system';
import Button from 'components/Button';
import errorImg from 'assets/images/error.svg';

export const StyledPlaceholder = styled.div`
  height: calc(100vh - 21rem);

  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;

  background-image: url(${errorImg});
  background-repeat: no-repeat;
  background-position: center 13rem;

  padding-top: 27rem;
`;

export const StyledParagraph = styled.p`
  font-size: 1.6rem;
  line-height: 2.4rem;

  margin: 0 0 3rem;
`;

export const StyledButton = styled(Button)`
  margin: 6rem 0 4rem !important;
`;

export const StyledCol = styled(Col)`
  button {
    margin-left: -1.5rem !important;
  }
`;
