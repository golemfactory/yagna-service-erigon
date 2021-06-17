import { useCallback, useEffect, useMemo, useState } from 'react';
import { Row } from 'react-grid-system';
import { useWeb3React } from '@web3-react/core';
import { Button, Layout, notify, Toast } from 'components';
import { useToggle } from 'hooks/useToggle';
import { Node, NodeForm, NodeFormData, NodeProps } from './components';
import httpRequest from 'utils/httpRequest';
import { StyledButton, StyledCol, StyledParagraph, StyledPlaceholder } from './styles';

const DashboardPage = () => {
  const [nodes, setNodes] = useState<NodeProps[]>([]);

  const nodeForm = useToggle({});

  const { account } = useWeb3React();

  const handleError = () => {
    setNodes([]);
    notify(<Toast />, 'error');
  };

  const handleFetchNodes = useCallback(
    async () =>
      await httpRequest({ method: 'get', path: 'getInstances', account })
        .then((instances: NodeProps[]) => setNodes(instances))
        .catch(handleError),
    [account],
  );

  useEffect(() => {
    handleFetchNodes();
  }, [handleFetchNodes]);

  useEffect(() => {
    const timer = setTimeout(() => {
      handleFetchNodes();
    }, 2000);

    return () => clearTimeout(timer);
  });

  const handleStartNode = ({ name, network }: NodeFormData) => {
    nodeForm.toggleOpen && nodeForm.toggleClick();

    httpRequest({ path: 'createInstance', account, data: { name, params: { network } } })
      .then(() => handleFetchNodes())
      .catch(handleError);
  };

  const handleStopNode = (id: string) =>
    httpRequest({ path: 'stopInstance', id, account })
      .then(() => handleFetchNodes())
      .catch(handleError);

  return (
    <Layout>
      {nodeForm.toggleOpen ? (
        <>
          <Row>
            <StyledCol xs={4} offset={{ xs: 8 }}>
              <StyledButton label="Cancel" onClick={nodeForm.toggleClick} outlined />
            </StyledCol>
          </Row>
          <NodeForm onSubmit={handleStartNode} />
        </>
      ) : !!nodes.length ? (
        <>
          <StyledButton label="Run new node" onClick={nodeForm.toggleClick} outlined />
          {nodes.map((node: NodeProps) => (
            <Node key={node.id} node={node}>
              <Button label="Stop node" onClick={() => handleStopNode(node.id)} />
            </Node>
          ))}
        </>
      ) : (
        <StyledPlaceholder>
          <StyledParagraph>Ooops! It looks like you don't have any node currently running </StyledParagraph>
          <Button label="Start new node" onClick={nodeForm.toggleClick} />
        </StyledPlaceholder>
      )}
    </Layout>
  );
};

export default DashboardPage;
