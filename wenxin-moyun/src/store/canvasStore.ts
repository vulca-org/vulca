import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type PlaygroundMode = 'edit' | 'run' | 'traditions';
export type TraditionsTab = 'browse' | 'create';

/**
 * Creation Mode — unified concept replacing separate Mock/NB2 + HITL toggles.
 *
 *  preview  = Mock provider, no HITL  (instant, free, for layout preview)
 *  guided   = Real provider + HITL    (real images, pause for human review)
 *  generate = Real provider, no HITL  (real images, fully automatic)
 */
export type CreationMode = 'preview' | 'guided' | 'generate';

/** Derive backend provider + enableHitl from a CreationMode. */
export function creationModeToParams(mode: CreationMode): { provider: string; enableHitl: boolean } {
  switch (mode) {
    case 'preview':  return { provider: 'mock', enableHitl: false };
    case 'guided':   return { provider: 'nb2',  enableHitl: true  };
    case 'generate': return { provider: 'nb2',  enableHitl: false };
  }
}

interface CanvasState {
  playgroundMode: PlaygroundMode;
  currentSubject: string;
  currentTradition: string;
  creationMode: CreationMode;
  /** @deprecated — use creationMode. Kept for backward compat during transition. */
  currentProvider: string;
  /** @deprecated — use creationMode. Kept for backward compat during transition. */
  enableHitl: boolean;
  traditionsTab: TraditionsTab;
  traditionManuallySet: boolean;
  traditionClassifying: boolean;
}

interface CanvasActions {
  setPlaygroundMode: (mode: PlaygroundMode) => void;
  setCurrentSubject: (subject: string) => void;
  setCurrentTradition: (tradition: string) => void;
  setCreationMode: (mode: CreationMode) => void;
  /** @deprecated — use setCreationMode */
  setCurrentProvider: (provider: string) => void;
  /** @deprecated — use setCreationMode */
  setEnableHitl: (enabled: boolean) => void;
  setTraditionsTab: (tab: TraditionsTab) => void;
  setTraditionManuallySet: (manually: boolean) => void;
  setTraditionClassifying: (classifying: boolean) => void;
  resetCanvas: () => void;
}

const initialState: CanvasState = {
  playgroundMode: 'run',
  currentSubject: '',
  currentTradition: 'chinese_xieyi',
  creationMode: 'preview',
  currentProvider: 'mock',
  enableHitl: false,
  traditionsTab: 'browse',
  traditionManuallySet: false,
  traditionClassifying: false,
};

export const useCanvasStore = create<CanvasState & CanvasActions>()(
  devtools(
    (set, get) => ({
      ...initialState,

      setPlaygroundMode: (mode) => set({ playgroundMode: mode }),
      setCurrentSubject: (subject) => set({ currentSubject: subject }),
      setCurrentTradition: (tradition) => set({ currentTradition: tradition }),
      setCreationMode: (mode) => {
        const { provider, enableHitl } = creationModeToParams(mode);
        set({ creationMode: mode, currentProvider: provider, enableHitl });
      },
      setCurrentProvider: (provider) => set({ currentProvider: provider }),
      setEnableHitl: (enabled) => set({ enableHitl: enabled }),
      setTraditionsTab: (tab) => set({ traditionsTab: tab }),
      setTraditionManuallySet: (manually) => set({ traditionManuallySet: manually }),
      setTraditionClassifying: (classifying) => set({ traditionClassifying: classifying }),
      resetCanvas: () => {
        const cm = get().creationMode;
        set({ ...initialState, creationMode: cm, ...creationModeToParams(cm) });
      },
    }),
    { name: 'canvas-store' }
  )
);
