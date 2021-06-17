import { useForm } from 'react-hook-form';
import { Row } from 'react-grid-system';
import { upperFirst } from 'lodash';
import { NodeFormData } from './types';
import { network, node } from './values';
import { Button } from 'components';
import options from './options';
import { StyledCol, StyledField, StyledForm, StyledNetworks, StyledRadioField } from './styles';

const networks = [
  { id: 'mainnet', name: network.name, disabled: true },
  { id: 'kovan', name: network.name },
  { id: 'goerli', name: network.name },
  { id: 'ropsten', name: network.name },
  { id: 'rinkeby', name: network.name },
];

const NodeForm = ({ onSubmit }: { onSubmit: (data: NodeFormData) => void }) => {
  const defaultValues = { name: '', network: networks[2].id };

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    // @ts-ignore
  } = useForm(options({ defaultValues }));

  return (
    <StyledForm onSubmit={handleSubmit(onSubmit)} autoComplete="off">
      <Row>
        <StyledCol xs={4}>
          {/*// @ts-ignore*/}
          <StyledField error={errors[node.name]}>
            <label>{node.label}</label>
            {/*// @ts-ignore*/}
            <input type="text" {...register(node.name, { required: true })} />
            {/*// @ts-ignore*/}
            {errors[node.name] && <span>{node.message}</span>}
          </StyledField>
        </StyledCol>
        <StyledCol xs={4}>
          <label>{network.label}</label>
          <StyledNetworks>
            {networks.map(({ id, name, disabled }: { id: string; name: string; disabled?: boolean }) => (
              <StyledRadioField
                key={id}
                // @ts-ignore
                checked={watch(name) === id}
                disabled={disabled}
              >
                {/*// @ts-ignore*/}
                <input type="radio" hidden {...register(name)} id={`${name}_${id}`} value={id} disabled={disabled} />
                <label htmlFor={`${name}_${id}`}>{upperFirst(id)}</label>
              </StyledRadioField>
            ))}
          </StyledNetworks>
        </StyledCol>
        <StyledCol xs={4}>
          <Button type="submit" label="Start node" />
        </StyledCol>
      </Row>
    </StyledForm>
  );
};

export default NodeForm;
