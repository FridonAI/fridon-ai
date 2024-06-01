import { Registry } from 'src/data-providers/registry';
import { InterfaceSnippet } from '../interface';
import { PointsProviderType, UserPointsResponseType } from '../shared/types';

type Request = {
  walletAddress: string;
};

type Response = UserPointsResponseType[];

@Registry('kamino-points')
export class KaminoPoints extends InterfaceSnippet<Request, Response> {
  async execute(data: Request): Promise<Response> {
    console.log('data', data);

    const { walletAddress } = data;

    return await this.pointsFactory.getPoints(
      walletAddress,
      PointsProviderType.Kamino,
    );
  }
}
