import styled from 'styled-components';
import { Container } from 'react-grid-system';
import { FixedContainerMixin } from 'styles/mixins';

export const StyledLayout = styled.div<{ unset?: boolean }>`
  min-width: 100%;
  min-height: 100%;

  padding-top: 12rem;
  padding-bottom: 6rem;
`;

export const StyledContainer = styled(Container)`
  ${FixedContainerMixin};

  min-height: calc(100vh - 21rem);
`;
