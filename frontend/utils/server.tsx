import "server-only";
import { AIProvider } from "./client";
import { ReactNode } from "react";
import { Runnable } from "@langchain/core/runnables";
import { CompiledStateGraph } from "@langchain/langgraph";
import { createStreamableUI, createStreamableValue } from "ai/rsc";
import { StreamEvent } from "@langchain/core/tracers/log_stream";
import { GithubLoading, Github } from "@/components/prebuilt/github";
import { InvoiceLoading, Invoice } from "@/components/prebuilt/invoice";
import { CurrentWeatherLoading, CurrentWeather } from "@/components/prebuilt/weather";
import { AIMessage } from "@/ai/message";

type ToolComponent = {
  loading: (props?: any) => JSX.Element;
  final: (props?: any) => JSX.Element;
};

type ToolComponentMap = {
  [tool: string]: ToolComponent;
};

const TOOL_COMPONENT_MAP: ToolComponentMap = {
  "github-repo": {
    loading: (props?: any) => <GithubLoading {...props} />,
    final: (props?: any) => <Github {...props} />,
  },
  "invoice-parser": {
    loading: (props?: any) => <InvoiceLoading {...props} />,
    final: (props?: any) => <Invoice {...props} />,
  },
  "weather-data": {
    loading: (props?: any) => <CurrentWeatherLoading {...props} />,
    final: (props?: any) => <CurrentWeather {...props} />,
  },
};

/**
 * Executes `streamEvents` method on a runnable
 * and converts the generator to a RSC friendly stream
 *
 * @param runnable
 * @returns React node which can be sent to the client
 */
export function streamRunnableUI<RunInput, RunOutput>(
  runnable:
    | Runnable<RunInput, RunOutput>
    | CompiledStateGraph<RunInput, Partial<RunInput>>,
  inputs: RunInput,
) {
  const ui = createStreamableUI();
  const [lastEvent, resolve] = withResolvers<
    Array<any> | Record<string, any>
  >();

  (async () => {
    let lastEventValue: StreamEvent | null = null;

    const callbacks: Record<
      string,
      ReturnType<typeof createStreamableUI | typeof createStreamableValue>
    > = {};

    let selectedToolComponent: ToolComponent | null = null;
    let selectedToolUI: ReturnType<typeof createStreamableUI> | null = null;

    for await (const streamEvent of (
      runnable as Runnable<RunInput, RunOutput>
    ).streamEvents(inputs, {
      version: "v1",
    })) {
      const { output, chunk } = streamEvent.data;
      // console.log("output, chunk",output, chunk)
      // console.log("===========")
      // console.log("streamEvent.event",streamEvent.event,streamEvent.name)
      // console.log("===========")
      // console.log("streamEvent.name",streamEvent.name)
      const [type] = streamEvent.event.split("_").slice(2);
      // const [kind, type] = streamEvent.event.split("_").slice(1);

      /**
       * Handles the 'invoke_model' event by checking for tool calls in the output.
       * If a tool call is found and no tool component is selected yet, it sets the
       * selected tool component based on the tool type and appends its loading state to the UI.
       *
       * @param output - The output object from the 'invoke_model' event
       * 通过检查输出中的工具调用来处理“invoke_model”事件。
       * 如果找到工具调用并且尚未选择任何工具组件，则会设置
       * 根据工具类型选择工具组件并将其加载状态附加到 UI。
       *
       * @param output -“invoke_model”事件的输出对象
       */
      const handleInvokeModelEvent = (output: Record<string, any>) => {
        if ("tool_calls" in output && output.tool_calls.length > 0) {
          const toolCall = output.tool_calls[0];
          if (!selectedToolComponent && !selectedToolUI) {
            selectedToolComponent = TOOL_COMPONENT_MAP[toolCall.type];
            selectedToolUI = createStreamableUI(
              selectedToolComponent.loading(),
            );
            ui.append(selectedToolUI?.value);
          }
        }
      };

      /**
       * Handles the 'invoke_tools' event by updating the selected tool's UI
       * with the final state and tool result data.
       *
       * @param output - The output object from the 'invoke_tools' event
   
       *通过更新所选工具的 UI 来处理“invoke_tools”事件
       *包含最终状态和工具结果数据。
       *
       *@param output -“invoke_tools”事件的输出对象
       */
      const handleInvokeToolsEvent = (output: Record<string, any>) => {
        if (selectedToolUI && selectedToolComponent) {
          const toolData = output.tool_result;
          selectedToolUI.done(selectedToolComponent.final(toolData));
        }
      };

      /**
       * Handles the 'on_chat_model_stream' event by creating a new text stream
       * for the AI message if one doesn't exist for the current run ID.
       * It then appends the chunk content to the corresponding text stream.
       *
       * @param streamEvent - The stream event object
       * @param chunk - The chunk object containing the content
       *通过创建新的文本流来处理“on_chat_model_stream”事件
       *用于 AI 消息（如果当前运行 ID 不存在）。
       *然后它将块内容附加到相应的文本流。
       *
       *@param streamEvent -流事件对象
       *@param chunk -包含内容的块对象
       */
      const handleChatModelStreamEvent = (
        streamEvent: StreamEvent,
        chunk: Record<string, any>,
      ) => {
        if (!callbacks[streamEvent.run_id]) {
          const textStream = createStreamableValue();
          ui.append(<AIMessage value={textStream.value} />);
          callbacks[streamEvent.run_id] = textStream;
        }

        if (callbacks[streamEvent.run_id]) {
          callbacks[streamEvent.run_id].append(chunk.content);
        }
      };

      if (type === "end" && output && typeof output === "object") {
        if (streamEvent.name === "invoke_model") {
          handleInvokeModelEvent(output);
        } else if (streamEvent.name === "invoke_tools") {
          handleInvokeToolsEvent(output);
        }
      }

      if (
        streamEvent.event === "on_chat_model_stream" &&
        chunk &&
        typeof chunk === "object"
      ) {
        handleChatModelStreamEvent(streamEvent, chunk);
      }

      lastEventValue = streamEvent;
    }

    // resolve the promise, which will be sent
    // to the client thanks to RSC
    resolve(lastEventValue?.data.output);

    Object.values(callbacks).forEach((cb) => cb.done());
    ui.done();
  })();

  return { ui: ui.value, lastEvent };
}

/**
 * Polyfill to emulate the upcoming Promise.withResolvers
 */
export function withResolvers<T>() {
  let resolve: (value: T) => void;
  let reject: (reason?: any) => void;

  const innerPromise = new Promise<T>((res, rej) => {
    resolve = res;
    reject = rej;
  });

  // @ts-expect-error
  return [innerPromise, resolve, reject] as const;
}

/**
 * Expose these endpoints outside for the client
 * We wrap the functions in order to properly resolve importing
 * client components.
 *
 * TODO: replace with createAI instead, even though that
 * implicitly handles state management
 *
 * See https://github.com/vercel/next.js/pull/59615
 * @param actions
 */
export function exposeEndpoints<T extends Record<string, unknown>>(
  actions: T,
): {
  (props: { children: ReactNode }): Promise<JSX.Element>;
  $$types?: T;
} {
  return async function AI(props: { children: ReactNode }) {
    return <AIProvider actions={actions}>{props.children}</AIProvider>;
  };
}