import { BadRequestException, Injectable, Logger } from '@nestjs/common';
import { PrismaClientKnownRequestError } from '@prisma/client/runtime/library';
import { PrismaService } from 'nestjs-prisma';

@Injectable()
export class MediasService {
  private readonly logger = new Logger(MediasService.name);

  constructor(private readonly prisma: PrismaService) {}

  async followMedia(walletAddress: string, media: string): Promise<void> {
    try {
      await this.prisma.walletMedia.create({
        data: {
          walletId: walletAddress,
          mediaId: media,
        },
      });
    } catch (e) {
      if (e instanceof PrismaClientKnownRequestError) {
        if (e.code === 'P2002') {
          this.logger.error(
            `Media[${media}] already followed by wallet[${walletAddress}]`,
          );
          throw new BadRequestException(`You are already following ${media}`);
        }

        if (e.code === 'P2003') {
          this.logger.error(`${media} not found`);
          throw new BadRequestException(`Media ${media} not found`);
        }

        throw new BadRequestException(e.message);
      }
      this.logger.error(e);
    }
  }

  async unfollowMedia(walletAddress: string, media: string): Promise<void> {
    try {
      await this.prisma.walletMedia.delete({
        where: {
          walletId_mediaId: {
            mediaId: media,
            walletId: walletAddress,
          },
        },
      });
    } catch (e) {
      if (e instanceof PrismaClientKnownRequestError) {
        if (e.code === 'P2025') {
          this.logger.error(
            `Media[${media}] not followed by wallet[${walletAddress}]`,
          );
          throw new BadRequestException(`You are not following ${media}`);
        }

        this.logger.error(e.message);
        return;
      }
      this.logger.error(e);
    }
  }

  async getFollowedMedia(walletId: string): Promise<string[]> {
    const result = await this.prisma.walletMedia.findMany({
      where: { walletId },
    });

    return result.map((media) => media.mediaId);
  }

  async getMedias(): Promise<string[]> {
    const result = await this.prisma.media.findMany();

    return result.map((media) => media.id);
  }
}
