import styled from 'styled-components';
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

export const StyledButton = styled(Button)`
  position: absolute;
  top: 4rem;
  right: 7rem;
`;

export const StyledParagraph = styled.p`
  font-size: 1.6rem;
  line-height: 2.4rem;
  text-align: center;
`;
