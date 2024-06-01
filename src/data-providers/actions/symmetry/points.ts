import { PointsProviderType } from 'src/blockchain/utils/types';
import { InterfaceSnippet } from '../interface';
import { UserPointsResponseType } from '../shared/types';
import { Registry } from 'src/data-providers/registry';

type Request = {
  walletAddress: string;
};

type Response = UserPointsResponseType[];

@Registry('symmetry-points')
export class SymmetryPoints extends InterfaceSnippet<Request, Response> {
  async execute(data: Request): Promise<Response> {
    console.log('data', data);

    const { walletAddress } = data;

    return await this.pointsFactory.getPoints(
      walletAddress,
      PointsProviderType.Symmetry,
    );
  }
}
