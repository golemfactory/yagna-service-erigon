import { useCallback, useEffect, useState } from 'react';
import { orderBy } from 'lodash';
import { status } from './components/Node/statuses';
import { Button, Layout, notify, TabPanel, Tabs, Toast } from 'components';
import { useMetamask } from 'app/App';
import { useToggle } from 'hooks/useToggle';
import { Node, NodeForm, NodeFormData, NodeProps } from './components';
import httpRequest from 'utils/httpRequest';
import { StyledButton, StyledParagraph, StyledPlaceholder } from './styles';

const DashboardPage = () => {
  const initialState = { active: [], stopped: [] };
  const [{ active, stopped }, setNodes] = useState<{ active: NodeProps[]; stopped: NodeProps[] }>(initialState);

  const nodeForm = useToggle({});

  const { account, authTicket } = useMetamask();

  const handleError = () => {
    setNodes(initialState);
    notify(<Toast />, 'error');
  };

  const handleFetchNodes = useCallback(
    async () =>
      await httpRequest({ method: 'get', path: 'getInstances', authTicket })
        .then((instances: NodeProps[]) =>
          setNodes({
            active: orderBy(
              instances.filter((instance: NodeProps) => instance.status !== status.stopped),
              'created_at',
              'desc',
            ),
            stopped: orderBy(
              instances.filter((instance: NodeProps) => instance.status === status.stopped),
              'stopped_at',
              'desc',
            ),
          }),
        )
        .catch(handleError),
    [account, authTicket],
  );

  useEffect(() => {
    handleFetchNodes();
  }, [handleFetchNodes]);

  useEffect(() => {
    const timer = setTimeout(() => {
      handleFetchNodes();
    }, 5000);

    return () => clearTimeout(timer);
  });

  const handleStartNode = ({ name, network }: NodeFormData) => {
    nodeForm.toggleOpen && nodeForm.toggleClick();

    httpRequest({ path: 'createInstance', data: { name, params: { network } } })
      .then(() => handleFetchNodes())
      .catch(handleError);
  };

  const handleStopNode = (id: string) =>
    httpRequest({ path: 'stopInstance', id })
      .then(() =>
        setNodes({
          active: active.map((node: NodeProps) => (node.id === id ? { ...node, status: status.stopping } : node)),
          stopped,
        }),
      )
      .catch(handleError);

  return (
    <Layout>
      {nodeForm.toggleOpen ? (
        <NodeForm onSubmit={handleStartNode}>
          <Button label="Cancel" onClick={nodeForm.toggleClick} ghost />
        </NodeForm>
      ) : !!active.length || !!stopped.length ? (
        <Tabs
          count={{ active: active.length, stopped: stopped.length }}
          button={<StyledButton label="Run new node" onClick={nodeForm.toggleClick} outlined />}
        >
          <TabPanel>
            {!!active.length ? (
              active.map((node: NodeProps) => (
                <Node key={node.id} node={node}>
                  <Button label="Stop node" onClick={() => handleStopNode(node.id)} />
                </Node>
              ))
            ) : (
              <StyledParagraph style={{ margin: '8rem 0' }}>
                Ooops! It looks like you don't have any node currently running
              </StyledParagraph>
            )}
          </TabPanel>
          <TabPanel>
            {!!stopped.length ? (
              stopped.map((node: NodeProps) => <Node key={node.id} node={node} />)
            ) : (
              <StyledParagraph style={{ margin: '8rem 0' }}>
                Ooops! It looks like you don't have any node stopped
              </StyledParagraph>
            )}
          </TabPanel>
        </Tabs>
      ) : (
        <StyledPlaceholder>
          <StyledParagraph style={{ margin: '0 0 3rem' }}>
            Ooops! It looks like you don't have any node currently running
          </StyledParagraph>
          <Button label="Start new node" onClick={nodeForm.toggleClick} />
        </StyledPlaceholder>
      )}
    </Layout>
  );
};

export default DashboardPage;
