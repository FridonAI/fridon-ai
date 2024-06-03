import { Injectable } from '@nestjs/common';
// import { PrismaService } from 'nestjs-prisma';

export type AssignPluginDto = {
  userId: string;
  plugin: string;
};

@Injectable()
export class UserService {
  // constructor(private readonly prisma: PrismaService) {}

  async assignPlugin(_: AssignPluginDto) {
    // TODO: Implement this method
  }
}
