import { Row } from 'react-grid-system';
import erigolemLogo from 'assets/logo/erigolem_logo.svg';
import {
  ErrorPlaceholder,
  PendingPlaceholder,
  StyledButton,
  StyledCol,
  StyledContainer,
  StyledHeader,
  StyledHyperlink,
  StyledPlaceholder,
} from './styles';
import { AuthTicket } from '../../utils/httpRequest/httpRequest';

const Header = ({
  metamask,
  active,
  onNotify,
  authTicket,
}: {
  metamask: boolean;
  active: boolean;
  authTicket: AuthTicket;
  onNotify: () => void;
}) => (
  <StyledHeader>
    <StyledContainer>
      <Row>
        <StyledCol xs={4}>
          <img src={erigolemLogo} alt="erigolem logo" />
          {authTicket.status === 'authorized' ? (
            <div style={{ textAlign: 'center', paddingLeft: '1em' }}>{authTicket.account}</div>
          ) : null}
        </StyledCol>
        <StyledCol xs={4} offset={{ xs: 4 }}>
          {!metamask ? (
            <StyledHyperlink href="https://metamask.io/" label="Install Metamask" />
          ) : !active ? (
            <StyledButton type="button" onClick={onNotify}>
              Connect to Metamask
            </StyledButton>
          ) : authTicket.status === 'init' || authTicket.status === 'pending' ? (
            <PendingPlaceholder>Pending</PendingPlaceholder>
          ) : authTicket.status === 'error' ? (
            <ErrorPlaceholder placeholder={authTicket.error.toString()}>Error</ErrorPlaceholder>
          ) : (
            <StyledPlaceholder>Connected</StyledPlaceholder>
          )}
        </StyledCol>
      </Row>
    </StyledContainer>
  </StyledHeader>
);

export default Header;
