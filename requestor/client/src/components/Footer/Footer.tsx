import { Row } from 'react-grid-system';
import golemLogo from 'assets/logo/golem_logo.svg';
import { StyledCol, StyledContainer, StyledFooter, StyledImg } from './styles';

const Footer = () => (
  <StyledFooter>
    <StyledContainer>
      <Row>
        <StyledCol xs={4} offset={{ xs: 8 }}>
          Proudly powered by <StyledImg src={golemLogo} alt="golem logo" />
        </StyledCol>
      </Row>
    </StyledContainer>
  </StyledFooter>
);

export default Footer;
