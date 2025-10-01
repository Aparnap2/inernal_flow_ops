# Page snapshot

```yaml
- generic [ref=e3]:
  - generic [ref=e4]:
    - generic [ref=e5]: "[plugin:vite:esbuild]"
    - generic [ref=e6]: "Transform failed with 1 error: /home/aparna/Desktop/flow_ops/frontend/src/utils/logger.ts:182:51: ERROR: Expected \";\" but found \"went\""
  - generic [ref=e8] [cursor=pointer]: /home/aparna/Desktop/flow_ops/frontend/src/utils/logger.ts:182:51
  - generic [ref=e9]: "Expected \";\" but found \"went\" 180| if (this.state.hasError) { 181| // Render fallback UI if provided 182| return this.props.fallback || <div>Something went wrong. Please try again later.</div>; | ^ 183| } 184|"
  - generic [ref=e10]:
    - text: at failureErrorWithLog (
    - generic [ref=e11] [cursor=pointer]: /home/aparna/Desktop/flow_ops/frontend/node_modules/.pnpm/esbuild@0.25.10/node_modules/esbuild/lib/main.js:1467:15
    - text: ) at
    - generic [ref=e12] [cursor=pointer]: /home/aparna/Desktop/flow_ops/frontend/node_modules/.pnpm/esbuild@0.25.10/node_modules/esbuild/lib/main.js:736:50
    - text: at responseCallbacks.<computed> (
    - generic [ref=e13] [cursor=pointer]: /home/aparna/Desktop/flow_ops/frontend/node_modules/.pnpm/esbuild@0.25.10/node_modules/esbuild/lib/main.js:603:9
    - text: ) at handleIncomingPacket (
    - generic [ref=e14] [cursor=pointer]: /home/aparna/Desktop/flow_ops/frontend/node_modules/.pnpm/esbuild@0.25.10/node_modules/esbuild/lib/main.js:658:12
    - text: ) at Socket.readFromStdout (
    - generic [ref=e15] [cursor=pointer]: /home/aparna/Desktop/flow_ops/frontend/node_modules/.pnpm/esbuild@0.25.10/node_modules/esbuild/lib/main.js:581:7
    - text: ) at Socket.emit (node:events:519:28) at addChunk (node:internal
    - generic [ref=e16] [cursor=pointer]: /streams/readable:561:12
    - text: ) at readableAddChunkPushByteMode (node:internal
    - generic [ref=e17] [cursor=pointer]: /streams/readable:512:3
    - text: ) at Readable.push (node:internal
    - generic [ref=e18] [cursor=pointer]: /streams/readable:392:5
    - text: ) at Pipe.onStreamRead (node:internal
    - generic [ref=e19] [cursor=pointer]: /stream_base_commons:189:23
  - generic [ref=e20]:
    - text: Click outside, press
    - generic [ref=e21]: Esc
    - text: key, or fix the code to dismiss.
    - text: You can also disable this overlay by setting
    - code [ref=e22]: server.hmr.overlay
    - text: to
    - code [ref=e23]: "false"
    - text: in
    - code [ref=e24]: vite.config.dev.ts
    - text: .
```