import { Col, Row } from 'react-grid-system';
import { Button, Layout } from 'components';
import landingImg from 'assets/images/landing.svg';
import { StyledHeading, StyledImg, StyledParagraph } from './styles';

const ProductPage = ({ onNotify }: { onNotify: () => void }) => (
  <Layout>
    <Row>
      <Col xs={6}>
        <StyledHeading>Run ethereum nodes in seconds</StyledHeading>
        <StyledParagraph>
          Erigolem is one of the fastest ways to integrate into the ethereum network. Select the type of network, click
          "start" and enjoy access to the most popular blockchain network in the world. Done.
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
