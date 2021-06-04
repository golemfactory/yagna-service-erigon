import styled from 'styled-components';
import { Col } from 'react-grid-system';
import color from 'styles/colors';
import addOpacityToColor from 'utils/addOpacityToColor';
import { status } from '../Node/statuses';
import copy from 'assets/icons/copy.svg';

export const StyledNode = styled.div`
  border: 0.1rem solid ${color.ash};
  box-shadow: 0 0.2rem 0.6rem 0 ${addOpacityToColor(color.black, 10)};
  border-radius: 1.4rem;

  margin-bottom: 4rem;
  padding: 6rem 4rem 0;
`;

export const StyledCol = styled(Col)`
  display: flex;
  flex-direction: column;

  padding-bottom: 6rem;

  > div {
    display: flex;
    justify-content: space-between;

    font-family: 'Inter Bold', sans-serif;

    margin-bottom: 2rem;
  }
`;

export const StyledName = styled.span`
  font-family: 'Roboto Mono Bold', monospace;
  font-size: 1.8rem;
  line-height: 2.4rem;
`;

export const StyledNetwork = styled.span`
  font-size: 1.4rem;
  line-height: 2.4rem;
`;

const statusColor = (state: string) => {
  switch (state) {
    case status.running:
      return color.green;
    case status.stopped:
      return color.red;
    default:
      return color.yellow;
  }
};

export const StyledStatus = styled.span<{ state: string }>`
  position: relative;

  line-height: 2.4rem;

  padding-left: 2.2rem;

  :before {
    content: '';

    width: 1.2rem;
    height: 1.2rem;

    position: absolute;
    top: 0.7rem;
    left: 0;

    background-color: ${({ state }) => statusColor(state)};
    border-radius: 50%;
  }
`;

export const StyledCopy = styled.span`
  color: ${color.blue};
  font-family: 'Inter Medium', sans-serif;
  font-size: 1rem;
  line-height: 1.5rem;
  text-transform: uppercase;

  margin-right: 7rem;

  background-image: url(${copy});
  background-repeat: no-repeat;
  background-position: 98% 38%;

  padding-right: 2rem;

  cursor: pointer;
`;

export const StyledPassword = styled.span`
  display: flex;
  justify-content: space-between;

  margin-right: 7rem;

  img {
    height: 1.3rem;
  }
`;
