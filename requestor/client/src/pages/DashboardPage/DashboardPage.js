import { useCallback, useEffect, useMemo, useState } from 'react';
import { useWeb3React } from '@web3-react/core';
import httpRequest from '../../utils/httpRequest';

const DashboardPage = () => {
  const [nodes, setNodes] = useState([]);
  const [error, setError] = useState(undefined);

  const { account } = useWeb3React();

  const data = useMemo(() => ({ user_id: account }), [account]);

  const handleError = () => {
    setNodes([]);
    setError('Something went wrong!');
  };

  const handleFetchNodes = useCallback(
    async () =>
      await httpRequest({ path: 'getInstances', data })
        .then((instances) => {
          setNodes(instances);
          setError(undefined);
        })
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

  const handleStopNode = (id) =>
    httpRequest({ path: 'stopInstance', id, data })
      .then(() => handleFetchNodes())
      .catch(handleError);

  return (
    <div>
      <button type="button" onClick={handleStartNode}>
        Start your node
      </button>
      {!!nodes.length ? (
        nodes.map(({ id, status, url, auth }) => (
          <div key={id}>
            <span>{id}</span>
            <a href={url} target="_blank" rel="noopener noreferrer">
              {url}
            </a>
            {auth && (
              <>
                <span>{auth.user}</span>
                <span>{auth.password}</span>
              </>
            )}
            <span>{status}</span>
            {status !== 'stopped' && (
              <button type="button" onClick={() => handleStopNode(id)}>
                stop
              </button>
            )}
          </div>
        ))
      ) : (
        <div>Oops. It looks like you don't have any nodes running currently</div>
      )}
      {error}
    </div>
  );
};

export default DashboardPage;
