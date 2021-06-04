import { useCallback, useEffect, useMemo, useState } from 'react';
import { useWeb3React } from '@web3-react/core';
import { Button, Layout, notify, Toast } from 'components';
import { Node, NodeProps } from './components';
import httpRequest from 'utils/httpRequest';
import { StyledButton, StyledParagraph, StyledPlaceholder } from './styles';

const DashboardPage = () => {
  const [nodes, setNodes] = useState<NodeProps[]>([]);

  const { account } = useWeb3React();

  const data = useMemo(() => ({ user_id: account }), [account]);

  const handleError = () => {
    setNodes([]);
    notify(<Toast />, 'error');
  };

  const handleFetchNodes = useCallback(
    async () =>
      await httpRequest({ path: 'getInstances', data })
        .then((instances: NodeProps[]) => setNodes(instances))
        .catch(handleError),
    [data],
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

  const handleStartNode = () =>
    httpRequest({ path: 'createInstance', data: { ...data, name: 'Eri-G', params: { network: 'rinkeby' } } })
      .then(() => handleFetchNodes())
      .catch(handleError);

  const handleStopNode = (id: string) =>
    httpRequest({ path: 'stopInstance', id, data })
      .then(() => handleFetchNodes())
      .catch(handleError);

  return (
    <Layout>
      {!!nodes.length ? (
        <>
          <StyledButton label="Run new node" onClick={handleStartNode} outlined />
          {nodes.map((node: NodeProps) => (
            <Node key={node.id} node={node}>
              <Button label="Stop node" onClick={() => handleStopNode(node.id)} />
            </Node>
          ))}
        </>
      ) : (
        <StyledPlaceholder>
          <StyledParagraph>Ooops! It looks like you don't have any node currently running </StyledParagraph>
          <Button label="Start new node" onClick={handleStartNode} />
        </StyledPlaceholder>
      )}
    </Layout>
  );
};

export default DashboardPage;
