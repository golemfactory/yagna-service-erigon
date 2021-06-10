import Web3 from 'web3';

export const getLibrary = () => new Web3(Web3.givenProvider);

export default getLibrary;
