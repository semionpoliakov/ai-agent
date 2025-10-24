import * as DialogPrimitive from "@radix-ui/react-dialog";
import { X } from "lucide-react";

import { cn } from "@/lib/utils";

export const Dialog = DialogPrimitive.Root;
export const DialogTrigger = DialogPrimitive.Trigger;
export const DialogClose = DialogPrimitive.Close;

export function DialogContent({ className, ...props }: DialogPrimitive.DialogContentProps) {
  return (
    <DialogPrimitive.Portal>
      <DialogPrimitive.Overlay className="fixed inset-0 bg-black/30 backdrop-blur-sm" />
      <DialogPrimitive.Content
        className={cn(
          "fixed inset-0 m-auto flex h-fit max-h-[80vh] w-full max-w-2xl flex-col gap-4 rounded-xl bg-card p-6 shadow-2xl",
          className,
        )}
        {...props}
      >
        <DialogPrimitive.Close className="absolute right-4 top-4 rounded-full p-1 text-muted-foreground transition hover:bg-muted">
          <X size={16} />
          <span className="sr-only">Close dialog</span>
        </DialogPrimitive.Close>
        {props.children}
      </DialogPrimitive.Content>
    </DialogPrimitive.Portal>
  );
}

export const DialogTitle = DialogPrimitive.Title;
export const DialogDescription = DialogPrimitive.Description;
