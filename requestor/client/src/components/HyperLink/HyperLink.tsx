import { StyledHyperLink } from './styles';

const HyperLink = ({ href, label, ...props }: { href: string; label: string }) => (
  <StyledHyperLink href={href} target="_blank" rel="noopener noreferrer" {...props}>
    {label}
  </StyledHyperLink>
);

export default HyperLink;
