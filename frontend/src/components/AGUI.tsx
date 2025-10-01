import React from 'react';
import { CopilotChat } from '@copilotkit/react-ui';
import { 
  useCopilotAction,
  useCopilotReadable 
} from '@copilotkit/react-core';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { logger } from '../utils/logger';
import { AGUIState, Run, Approval, Exception } from '../types';
import { apiService } from '../api';
import { Play, Pause, RotateCcw, Settings } from 'lucide-react';

interface AGUIProps {
  className?: string;
}

const AGUI: React.FC<AGUIProps> = ({ className }) => {
  // Initialize the AGUI state agent
  const { state, setState } = useCoAgent<AGUIState>({
    name: "agui_state",
    initialState: {
      activeRuns: [],
      pendingApprovals: [],
      openExceptions: [],
      kpiData: {
        totalRuns: 0,
        successfulRuns: 0,
        pendingApprovals: 0,
        openExceptions: 0
      }
    }
  });

  // Use the state for display
  const agentState = useCoAgentState({
    name: "agui_state",
  });

  // Make functions actionable for the AI agent with error handling
  useMakeCopilotActionable({
    name: "approveWorkflow",
    description: "Approve a pending workflow for continuation",
    arguments: [
      {
        name: "runId",
        type: "string",
        description: "The ID of the workflow run to approve"
      }
    ],
    handler: async ({ runId }: { runId: string }) => {
      try {
        logger.info(`Approving workflow run ${runId}`);
        
        // In a real implementation, this would call your API to approve the workflow
        const result = await apiService.approveRun(runId, true);
        
        setState(prev => ({
          ...prev,
          pendingApprovals: prev.pendingApprovals.filter(a => a.id !== runId),
          kpiData: {
            ...prev.kpiData,
            pendingApprovals: prev.kpiData.pendingApprovals - 1
          }
        }));
        
        logger.info(`Successfully approved workflow run ${runId}`);
        return { status: "success", message: `Run ${runId} approved` };
      } catch (error) {
        logger.error(`Failed to approve workflow run ${runId}`, { 
          error: error instanceof Error ? error.message : String(error),
          runId 
        });
        return { 
          status: "error", 
          message: `Failed to approve run ${runId}: ${error instanceof Error ? error.message : String(error)}` 
        };
      }
    }
  });

  useMakeCopilotActionable({
    name: "rejectWorkflow",
    description: "Reject a pending workflow",
    arguments: [
      {
        name: "runId",
        type: "string",
        description: "The ID of the workflow run to reject"
      },
      {
        name: "reason",
        type: "string",
        description: "The reason for rejection"
      }
    ],
    handler: async ({ runId, reason }: { runId: string; reason: string }) => {
      try {
        logger.info(`Rejecting workflow run ${runId}`, { reason });
        
        // In a real implementation, this would call your API to reject the workflow
        const result = await apiService.approveRun(runId, false, reason);
        
        setState(prev => ({
          ...prev,
          pendingApprovals: prev.pendingApprovals.filter(a => a.id !== runId),
          kpiData: {
            ...prev.kpiData,
            pendingApprovals: prev.kpiData.pendingApprovals - 1
          }
        }));
        
        logger.info(`Successfully rejected workflow run ${runId}`);
        return { status: "success", message: `Run ${runId} rejected` };
      } catch (error) {
        logger.error(`Failed to reject workflow run ${runId}`, { 
          error: error instanceof Error ? error.message : String(error),
          runId,
          reason
        });
        return { 
          status: "error", 
          message: `Failed to reject run ${runId}: ${error instanceof Error ? error.message : String(error)}` 
        };
      }
    }
  });

  useMakeCopilotActionable({
    name: "resolveException",
    description: "Resolve an exception with a specified resolution type",
    arguments: [
      {
        name: "exceptionId",
        type: "string",
        description: "The ID of the exception to resolve"
      },
      {
        name: "resolutionType",
        type: "string",
        description: "The type of resolution to apply (AUTO_REPAIR, MANUAL_FIX, IGNORE, ESCALATE)"
      }
    ],
    handler: async ({ exceptionId, resolutionType }: { exceptionId: string; resolutionType: string }) => {
      try {
        logger.info(`Resolving exception ${exceptionId}`, { resolutionType });
        
        // In a real implementation, this would call your API to resolve the exception
        const result = await apiService.resolveException(exceptionId, resolutionType);
        
        setState(prev => ({
          ...prev,
          openExceptions: prev.openExceptions.filter(e => e.id !== exceptionId),
          kpiData: {
            ...prev.kpiData,
            openExceptions: prev.kpiData.openExceptions - 1
          }
        }));
        
        logger.info(`Successfully resolved exception ${exceptionId}`);
        return { status: "success", message: `Exception ${exceptionId} resolved` };
      } catch (error) {
        logger.error(`Failed to resolve exception ${exceptionId}`, { 
          error: error instanceof Error ? error.message : String(error),
          exceptionId,
          resolutionType
        });
        return { 
          status: "error", 
          message: `Failed to resolve exception ${exceptionId}: ${error instanceof Error ? error.message : String(error)}` 
        };
      }
    }
  });

  useMakeCopilotActionable({
    name: "pauseWorkflow",
    description: "Pause a running workflow",
    arguments: [
      {
        name: "runId",
        type: "string",
        description: "The ID of the workflow run to pause"
      }
    ],
    handler: async ({ runId }: { runId: string }) => {
      try {
        logger.info(`Pausing workflow run ${runId}`);
        
        // In a real implementation, this would call your backend AI service to pause the workflow
        // const result = await callAIService('pause-workflow', { runId });
        
        setState(prev => ({
          ...prev,
          activeRuns: prev.activeRuns.map(run => 
            run.id === runId ? { ...run, status: 'CANCELLED' } : run
          )
        }));
        
        logger.info(`Successfully paused workflow run ${runId}`);
        return { status: "success", message: `Run ${runId} paused` };
      } catch (error) {
        logger.error(`Failed to pause workflow run ${runId}`, { 
          error: error instanceof Error ? error.message : String(error),
          runId 
        });
        return { 
          status: "error", 
          message: `Failed to pause run ${runId}: ${error instanceof Error ? error.message : String(error)}` 
        };
      }
    }
  });

  useMakeCopilotActionable({
    name: "restartWorkflow",
    description: "Restart a failed workflow from the last checkpoint",
    arguments: [
      {
        name: "runId",
        type: "string",
        description: "The ID of the workflow run to restart"
      }
    ],
    handler: async ({ runId }: { runId: string }) => {
      try {
        logger.info(`Restarting workflow run ${runId} from last checkpoint`);
        
        // In a real implementation, this would call your backend AI service to restart the workflow
        // const result = await callAIService('restart-workflow', { runId });
        
        setState(prev => ({
          ...prev,
          activeRuns: prev.activeRuns.map(run => 
            run.id === runId ? { ...run, status: 'RUNNING' } : run
          )
        }));
        
        logger.info(`Successfully restarted workflow run ${runId}`);
        return { status: "success", message: `Run ${runId} restarted` };
      } catch (error) {
        logger.error(`Failed to restart workflow run ${runId}`, { 
          error: error instanceof Error ? error.message : String(error),
          runId 
        });
        return { 
          status: "error", 
          message: `Failed to restart run ${runId}: ${error instanceof Error ? error.message : String(error)}` 
        };
      }
    }
  });

  useMakeCopilotActionable({
    name: "getRunDetails",
    description: "Get detailed information about a specific workflow run",
    arguments: [
      {
        name: "runId",
        type: "string",
        description: "The ID of the workflow run to get details for"
      }
    ],
    handler: async ({ runId }: { runId: string }) => {
      try {
        logger.info(`Fetching details for workflow run ${runId}`);
        
        // In a real implementation, this would call your API to get run details
        // const runDetails = await apiService.getRunById(runId);
        
        // For demo purposes, returning mock data
        const runDetails = {
          id: runId,
          workflowId: 'company-intake',
          status: 'RUNNING',
          startedAt: new Date().toISOString(),
          currentStep: 'normalize_company_data',
          completedSteps: ['start_intake', 'extract_company_data'],
          nextStep: 'upsert_to_airtable',
          checkpointData: { currentStep: 'normalize_company_data' }
        };
        
        return { status: "success", data: runDetails };
      } catch (error) {
        logger.error(`Failed to fetch details for workflow run ${runId}`, { 
          error: error instanceof Error ? error.message : String(error),
          runId 
        });
        return { 
          status: "error", 
          message: `Failed to fetch details for run ${runId}: ${error instanceof Error ? error.message : String(error)}` 
        };
      }
    }
  });

  return (
    <Card className={className}>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center">
            <span className="mr-2">🤖</span>
            Agentic UI Assistant
          </div>
          <div className="flex space-x-1">
            <Button variant="outline" size="sm" onClick={() => {
              // Refresh state from backend
              logger.info("Refreshing AGUI state from backend");
              console.log("Refreshing state from backend");
            }}>
              <RotateCcw className="h-4 w-4" />
            </Button>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="text-sm text-muted-foreground">
          Interact with the system using natural language. The assistant can help you approve workflows, resolve exceptions, and manage operations.
        </div>
        
        <CopilotTextarea
          label="Commands"
          placeholder="Try: 'Approve all critical pending workflows', 'Show me failed runs from last hour', or 'Restart failed workflow for company XYZ'..."
          className="w-full p-3 border rounded-md min-h-[100px]"
          name="agui_commands"
        />
        
        <div className="grid grid-cols-2 gap-2">
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => {
              logger.info("Getting status via AGUI command");
              console.log("Getting status via AGUI command");
            }}
          >
            Get Status
          </Button>
          <Button 
            variant="outline" 
            size="sm"
            onClick={() => {
              logger.info("Resolving exceptions via AGUI command");
              console.log("Resolving exceptions via AGUI command");
            }}
          >
            Resolve Exceptions
          </Button>
        </div>
        
        <div className="pt-4 border-t">
          <div className="font-medium text-sm mb-2">Quick Actions:</div>
          <div className="grid grid-cols-2 gap-2">
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                logger.info("Approving all pending via AGUI command");
                console.log("Approving all pending");
              }}
            >
              Approve All Pending
            </Button>
            <Button 
              variant="outline" 
              size="sm"
              onClick={() => {
                logger.info("Auto-repair exceptions via AGUI command");
                console.log("Auto-repair exceptions");
              }}
            >
              Auto-repair Exceptions
            </Button>
          </div>
        </div>
        
        <div className="pt-4 border-t">
          <div className="font-medium text-sm mb-2">Current Metrics:</div>
          <div className="grid grid-cols-2 gap-4 text-xs">
            <div className="flex justify-between">
              <span>Pending Approvals:</span>
              <span className="font-medium">{state.kpiData.pendingApprovals}</span>
            </div>
            <div className="flex justify-between">
              <span>Open Exceptions:</span>
              <span className="font-medium">{state.kpiData.openExceptions}</span>
            </div>
            <div className="flex justify-between">
              <span>Total Runs:</span>
              <span className="font-medium">{state.kpiData.totalRuns}</span>
            </div>
            <div className="flex justify-between">
              <span>Success Rate:</span>
              <span className="font-medium">
                {state.kpiData.totalRuns > 0 
                  ? Math.round((state.kpiData.successfulRuns / state.kpiData.totalRuns) * 100) 
                  : 0}%
              </span>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default AGUI;