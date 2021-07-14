import styled from 'styled-components';
import { Col, Container } from 'react-grid-system';
import { FixedContainerMixin } from 'styles/mixins';

export const StyledFooter = styled.div`
  width: 100%;
  height: 6rem;

  position: absolute;
  left: 0;
  right: 0;
  bottom: 0;

  font-size: 1rem;
  line-height: 2.2rem;

  padding-top: 1.5rem;
`;

export const StyledContainer = styled(Container)`
  ${FixedContainerMixin};

  height: 2.6rem;
`;

export const StyledCol = styled(Col)`
  height: 2.6rem;

  display: flex;
  justify-content: flex-end;
  align-items: center;
`;

export const StyledImg = styled.img`
  height: 2.6rem;

  margin-left: 1rem;
`;
