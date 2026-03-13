import { create } from 'zustand';
import { devtools } from 'zustand/middleware';

export type PlaygroundMode = 'edit' | 'run' | 'traditions';
export type TraditionsTab = 'browse' | 'create';

interface CanvasState {
  playgroundMode: PlaygroundMode;
  currentSubject: string;
  currentTradition: string;
  currentProvider: string;
  enableHitl: boolean;
  traditionsTab: TraditionsTab;
  traditionManuallySet: boolean;
  traditionClassifying: boolean;
}

interface CanvasActions {
  setPlaygroundMode: (mode: PlaygroundMode) => void;
  setCurrentSubject: (subject: string) => void;
  setCurrentTradition: (tradition: string) => void;
  setCurrentProvider: (provider: string) => void;
  setEnableHitl: (enabled: boolean) => void;
  setTraditionsTab: (tab: TraditionsTab) => void;
  setTraditionManuallySet: (manually: boolean) => void;
  setTraditionClassifying: (classifying: boolean) => void;
  resetCanvas: () => void;
}

const initialState: CanvasState = {
  playgroundMode: 'edit',
  currentSubject: '',
  currentTradition: 'chinese_xieyi',
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
      setCurrentProvider: (provider) => set({ currentProvider: provider }),
      setEnableHitl: (enabled) => set({ enableHitl: enabled }),
      setTraditionsTab: (tab) => set({ traditionsTab: tab }),
      setTraditionManuallySet: (manually) => set({ traditionManuallySet: manually }),
      setTraditionClassifying: (classifying) => set({ traditionClassifying: classifying }),
      resetCanvas: () => {
        const provider = get().currentProvider;
        set({ ...initialState, currentProvider: provider });
      },
    }),
    { name: 'canvas-store' }
  )
);
