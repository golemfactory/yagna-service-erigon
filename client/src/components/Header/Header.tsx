import { Row } from 'react-grid-system';
import erigolemLogo from 'assets/logo/erigolem_logo.svg';
import { StyledButton, StyledCol, StyledContainer, StyledHeader, StyledHyperlink, StyledPlaceholder } from './styles';

const Header = ({ metamask, active, onNotify }: { metamask: boolean; active: boolean; onNotify: () => void }) => (
  <StyledHeader>
    <StyledContainer>
      <Row>
        <StyledCol xs={4}>
          <img src={erigolemLogo} alt="erigolem logo" />
        </StyledCol>
        <StyledCol xs={4} offset={{ xs: 4 }}>
          {!metamask ? (
            <StyledHyperlink href="https://metamask.io/" label="Install Metamask" />
          ) : !active ? (
            <StyledButton type="button" onClick={onNotify}>
              Connect to Metamask
            </StyledButton>
          ) : (
            <StyledPlaceholder>Connected</StyledPlaceholder>
          )}
        </StyledCol>
      </Row>
    </StyledContainer>
  </StyledHeader>
);

export default Header;
