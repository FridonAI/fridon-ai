import {
  OnGatewayConnection,
  OnGatewayDisconnect,
  WebSocketGateway,
} from '@nestjs/websockets';
import { Injectable } from '@nestjs/common';
import { Socket } from 'socket.io';

@WebSocketGateway({ cors: { origin: '*' } })
@Injectable()
export class EventsGateway implements OnGatewayConnection, OnGatewayDisconnect {
  private sockets: Map<string, Socket[]> = new Map();

  async handleConnection(client: Socket) {
    const { walletId } = this.getClientInfoFromAuth(client);

    const key = walletId;
    if (!this.sockets.has(key)) {
      this.sockets.set(key, []);
    }

    this.sockets.get(key)?.push(client);
  }

  async handleDisconnect(client: Socket) {
    const { walletId } = this.getClientInfoFromAuth(client);

    const key = walletId;
    const sockets = this.sockets.get(key);
    if (sockets) {
      const index = sockets.indexOf(client);
      if (index > -1) {
        sockets.splice(index, 1);
      }
    }
  }

  public sendTo(walletId: string, event: string, data: any) {
    this.sockets.get(walletId)?.forEach((socket) => socket.emit(event, data));
  }

  private getClientInfoFromAuth(_: Socket): { walletId: string } {
    return {
      walletId: 'RANDOM_WALLET_ID',
    };
  }
}
