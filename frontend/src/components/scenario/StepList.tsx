import { useState } from 'react';
import { DndContext, PointerSensorContext, useDraggable, useDroppable, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, SortableContext, arrayMove, useSortable, verticalListSortingStrategy } from '@dnd-kit/sortable';
import { SortableContext as SortableContextType, SortableContext } from '@dnd-kit/sortable';
import { GripVertical, Trash2, Edit2 } from 'lucide-react';
import type { ScenarioStep } from '@/types/scenario';

interface StepListProps {
  steps: ScenarioStep[];
  onReorder: (oldIndex: number, newIndex: number) => void;
  onDelete: (stepId: number) => void;
  onEdit: (step: ScenarioStep) => void;
}

export default function StepList({ steps, onReorder, onDelete, onEdit }: StepListProps) {
  const [activeId, setActiveId] = useState<number | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8,
      },
    })
  );

  const {
    attributes: listenAttributes,
    setNodeRef: setDroppableNodeRef,
  } = useDroppable({
    id: 'steps-list',
  });

  return (
    <DndContext sensors={sensors}>
      <SortableContext items={steps.map(s => s.id)}>
        <SortableContextType>
          <div
            {...listenAttributes}
            ref={setDroppableNodeRef}
            className="space-y-3"
          >
            {steps.map((step, index) => (
              <SortableStep
                key={step.id}
                step={step}
                index={index}
                activeId={activeId}
                setActiveId={setActiveId}
                onReorder={onReorder}
                onDelete={onDelete}
                onEdit={onEdit}
              />
            ))}
          </div>
        </SortableContextType>
      </DndContext>
    </div>
  );
}

interface SortableStepProps {
  step: ScenarioStep;
  index: number;
  activeId: number | null;
  setActiveId: (id: number | null) => void;
  onReorder: (oldIndex: number, newIndex: number) => void;
  onDelete: (stepId: number) => void;
  onEdit: (step: ScenarioStep) => void;
}

function SortableStep({
  step,
  index,
  activeId,
  setActiveId,
  onReorder,
  onDelete,
  onEdit,
}: SortableStepProps) {
  const {
    attributes,
    isDragging,
    listeners,
    setNodeRef,
    transform,
    transition,
  } = useSortable({
    id: step.id,
    index,
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  const handleKeyDown = (event: React.KeyboardEvent) => {
    if (event.key === 'Delete' || event.key === 'Backspace') {
      event.preventDefault();
      onDelete(step.id);
    }
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      className={\`group relative bg-white rounded-lg border \${isDragging ? 'border-blue-500 shadow-lg' : 'border-gray-200 hover:border-gray-300'} p-4 transition-all\`}
    >
      {/* 拖拽手柄 */}
      <button
        {...attributes}
        {...listeners}
        aria-label="拖拽步骤"
        onKeyDown={handleKeyDown}
        className="absolute left-0 top-1/2 -translate-y-1/2 p-1 cursor-grab hover:bg-gray-100 rounded"
      >
        <GripVertical size={16} className="text-gray-400" />
      </button>

      {/* 步骤内容 */}
      <div className="pl-10">
        <div className="flex items-start justify-between mb-2">
          <div className="flex-1">
            <div className="flex items-center gap-2 mb-2">
              <span className={\`inline-flex items-center justify-center w-6 h-6 rounded-full text-xs font-semibold \${activeId === step.id ? 'bg-blue-600 text-white' : 'bg-gray-200 text-gray-700'}\`}>
                {index + 1}
              </span>
              <h3 className="text-lg font-semibold text-gray-900">{step.description}</h3>
            </div>
            <p className="text-sm text-gray-600">
              关键字 ID: {step.keyword_id}
            </p>
          </div>
        </div>

        {/* 参数预览 */}
        {Object.keys(step.params).length > 0 && (
          <div className="mt-2 text-sm bg-gray-50 rounded p-2">
            <p className="font-medium text-gray-700 mb-1">参数:</p>
            <div className="space-y-1">
              {Object.entries(step.params).slice(0, 3).map(([key, value]) => (
                <div key={key} className="text-gray-600">
                  <span className="font-mono text-xs bg-gray-200 px-1 rounded">{key}</span>
                  <span className="ml-2">: {JSON.stringify(value)}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* 操作按钮 */}
        <div className="flex items-center gap-2 mt-3 opacity-0 group-hover:opacity-100 transition-opacity">
          <button
            onClick={() => onEdit(step)}
            className="p-1.5 hover:bg-gray-100 rounded text-gray-600"
            title="编辑步骤"
          >
            <Edit2 size={16} />
          </button>
          <button
            onClick={() => onDelete(step.id)}
            className="p-1.5 hover:bg-red-50 rounded text-red-600"
            title="删除步骤"
          >
            <Trash2 size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}
