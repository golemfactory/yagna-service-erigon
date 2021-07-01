export enum status {
  pending = 'pending',
  starting = 'starting',
  running = 'running',
  stopping = 'stopping',
  stopped = 'stopped',
}

export const statues = [status.starting, status.pending, status.running, status.stopping, status.stopped];
