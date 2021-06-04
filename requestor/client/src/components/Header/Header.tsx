import { useWeb3React } from '@web3-react/core';

const Header = ({ metamask }: { metamask: boolean }) => {
  const { active } = useWeb3React();

  return (
    <div>
      {!metamask ? (
        <a href="https://metamask.io/" target="_blank" rel="noopener noreferrer">
          Install Metamask
        </a>
      ) : !active ? (
        <button type="button" onClick={() => console.log('Process with Metamask login')}>
          Connect to Metamask
        </button>
      ) : (
        <span>Connected</span>
      )}
    </div>
  );
};

export default Header;
