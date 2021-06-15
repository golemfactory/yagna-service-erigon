import { ReactNode } from 'react';
import { Col, Row } from 'react-grid-system';
import { CopyToClipboard } from 'react-copy-to-clipboard';
import { upperFirst } from 'lodash';
import { NodeProps } from './types';
import { status } from './statuses';
import { HyperLink, notify, Toast } from 'components';
import { useToggle } from 'hooks/useToggle';
import eyeClosed from 'assets/icons/eye-closed.svg';
import eyeOpen from 'assets/icons/eye-open.svg';
import { StyledCol, StyledCopy, StyledName, StyledNetwork, StyledNode, StyledStatus, StyledPassword } from './styles';

const Node = ({ node, children }: { node: NodeProps; children: ReactNode }) => {
  const handleCopy = () => notify(<Toast message="Copied!" />, 'success');

  const password = useToggle({});

  return (
    <StyledNode>
      <Row>
        <StyledCol xs={4}>
          <div>Node name</div>
          <StyledName>{node.name}</StyledName>
        </StyledCol>
        <StyledCol xs={4}>
          <div>Network</div>
          <StyledNetwork>{upperFirst(node.init_params.network)}</StyledNetwork>
        </StyledCol>
        <StyledCol xs={4}>
          <div>Status</div>
          <StyledStatus state={node.status}>{upperFirst(node.status)}</StyledStatus>
        </StyledCol>
      </Row>
      <Row>
        <StyledCol xs={4}>
          {node.url && (
            <>
              <div>
                Address
                <CopyToClipboard text={node.url} onCopy={handleCopy}>
                  <StyledCopy>Copy</StyledCopy>
                </CopyToClipboard>
              </div>
              <HyperLink href={node.url} label={node.url} />
            </>
          )}
        </StyledCol>
        <Col xs={4} offset={{ xs: 4 }}>
          {node.status !== status.stopped && children}
        </Col>
      </Row>
      <Row>
        <StyledCol xs={4}>
          {node.auth && (
            <>
              <div>
                Login
                <CopyToClipboard text={node.auth.user} onCopy={handleCopy}>
                  <StyledCopy>Copy</StyledCopy>
                </CopyToClipboard>
              </div>
              {node.auth.user}
            </>
          )}
        </StyledCol>
        <StyledCol xs={4}>
          {node.auth && (
            <>
              <div>
                Password
                <CopyToClipboard text={node.auth.password} onCopy={handleCopy}>
                  <StyledCopy>Copy</StyledCopy>
                </CopyToClipboard>
              </div>
              <StyledPassword>
                {password.toggleOpen ? node.auth.password : '*'.repeat(node.auth.password.length)}
                <img src={password.toggleOpen ? eyeClosed : eyeOpen} alt="toggle icon" onClick={password.toggleClick} />
              </StyledPassword>
            </>
          )}
        </StyledCol>
      </Row>
    </StyledNode>
  );
};

export default Node;
