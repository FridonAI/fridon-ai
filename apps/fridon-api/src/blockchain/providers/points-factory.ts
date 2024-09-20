import { HttpException } from '@nestjs/common';
import { PointsProviderType } from '../utils/types';

export type UserPointsResponseType = {
  walletAddress: string;
  points: number;
  provider: PointsProviderType;
};

export class PointsFactory {
  async getKaminoPoints(walletAddress: string) {
    try {
      const request = await fetch(
        `https://api.hubbleprotocol.io/points/users/${walletAddress}/breakdown?env=mainnet-beta&source=Season1`,
      );
      const response = await request.json();

      if (!response.totalPointsEarned) {
        return 0;
      }

      const totalPointsEarnedNumber = parseFloat(response.totalPointsEarned);
      return Math.round(totalPointsEarnedNumber * 100) / 100;
    } catch (error) {
      console.error('Error while fetching user points', error);
      throw new HttpException('Error while fetching user points', 403);
    }
  }

  async getSymmetryPoints(walletAddress: string) {
    try {
      const request = await fetch('https://api.symmetry.fi/v1/funds-getter', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          request: 'get_user',
          params: {
            pubkey: walletAddress,
          },
        }),
      });

      const response = await request.json();
      if (!response?.total_points) {
        return 0;
      }
      return response.total_points as number;
    } catch (error) {
      console.error('Error while fetching user points', error);
      return 0;
    }
  }

  async getDriftPoints(walletAddress: string) {
    try {
      const request = await fetch(
        `https://app.drift.trade/api/points-drop?authority=${walletAddress}`,
      );
      const response = await request.json();

      if (!response?.data?.latestDrop?.authorityScore) {
        return 0;
      }
      const points = response.data.latestDrop.authorityScore;

      return points as number;
    } catch (error) {
      console.error('Error while fetching user points', error);
      return 0;
    }
  }

  async getParclPoints(walletAddress: string) {
    try {
      const request = await fetch(
        `https://parcl-api.com/v1/points/balance?user=${walletAddress}`,
      );
      const response = await request.json();

      console.log('response', response);
      if (!response?.balance) {
        return 0;
      }
      return response.balance as number;
    } catch (error) {
      console.error('Error while fetching user points', error);
      return 0;
    }
  }

  async getPoints(walletAddress: string, provider: PointsProviderType) {
    const result: UserPointsResponseType[] = [];

    if (
      provider == PointsProviderType.Kamino ||
      provider == PointsProviderType.All
    ) {
      const userPoints = await this.getKaminoPoints(walletAddress);
      result.push({
        points: userPoints,
        walletAddress,
        provider: PointsProviderType.Kamino,
      });
    }

    if (
      provider == PointsProviderType.Symmetry ||
      provider == PointsProviderType.All
    ) {
      const userPoints = await this.getSymmetryPoints(walletAddress);
      result.push({
        points: userPoints,
        walletAddress,
        provider: PointsProviderType.Symmetry,
      });
    }

    if (
      provider == PointsProviderType.Drift ||
      provider == PointsProviderType.All
    ) {
      const userPoints = await this.getDriftPoints(walletAddress);
      result.push({
        points: userPoints,
        walletAddress,
        provider: PointsProviderType.Drift,
      });
    }

    return result;
  }
}
