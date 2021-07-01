import { Col, Row } from 'react-grid-system';
import { LayoutProps } from './types';
import { StyledContainer, StyledLayout } from './styles';

const Layout = ({ children, columns = { xs: 12 }, offset = { xs: 0 } }: LayoutProps) => (
  <StyledLayout>
    <StyledContainer>
      <Row>
        <Col {...columns} offset={offset}>
          {children}
        </Col>
      </Row>
    </StyledContainer>
  </StyledLayout>
);

export default Layout;
