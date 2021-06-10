import { Col, Row } from 'react-grid-system';
import { Button, Layout } from 'components';
import landingImg from 'assets/images/landing.svg';
import { StyledHeading, StyledImg, StyledParagraph } from './styles';

const ProductPage = ({ onNotify }: { onNotify: () => void }) => (
  <Layout>
    <Row>
      <Col xs={6}>
        <StyledHeading>Catchy and cool phrase</StyledHeading>
        <StyledParagraph>
          The Golem Network fosters a global group of creators building ambitious software solutions that will shape the
          technological landscape of future generations by accessing computing resources across the platform.
        </StyledParagraph>
        <Button label="Start new node" onClick={onNotify} />
      </Col>
      <Col xs={6}>
        <StyledImg src={landingImg} alt="image" />
      </Col>
    </Row>
  </Layout>
);

export default ProductPage;
