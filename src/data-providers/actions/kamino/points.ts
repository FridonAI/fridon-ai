import { Registry } from 'src/data-providers/registry';
import { InterfaceSnippet } from '../interface';
import { PointsProviderType, UserPointsResponseType } from '../shared/types';
import { Logger } from '@nestjs/common';

type Request = {
  walletAddress: string;
};

type Response = UserPointsResponseType[];

@Registry('kamino-points')
export class KaminoPoints extends InterfaceSnippet<Request, Response> {
  private logger = new Logger(KaminoPoints.name);

  async execute(data: Request): Promise<Response> {
    this.logger.log(`Executing action: ${KaminoPoints.name}`);

    const { walletAddress } = data;

    return await this.pointsFactory.getPoints(
      walletAddress,
      PointsProviderType.Kamino,
    );
  }
}
