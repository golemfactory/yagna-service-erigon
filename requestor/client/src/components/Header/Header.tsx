import { Row } from 'react-grid-system';
import { useWeb3React } from '@web3-react/core';
import { notify, Toast } from '../index';
import erigolemLogo from 'assets/logo/erigolem_logo.svg';
import { StyledButton, StyledCol, StyledContainer, StyledHeader, StyledHyperlink, StyledPlaceholder } from './styles';

const Header = ({ metamask }: { metamask: boolean }) => {
  const { active } = useWeb3React();

  const handleConnect = () => notify(<Toast code={-32002} />);

  return (
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
              <StyledButton type="button" onClick={handleConnect}>
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
};

export default Header;
