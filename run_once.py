from qiskit_ibm_runtime import QiskitRuntimeService
from dotenv import load_dotenv
import os
load_dotenv()
api_key = os.getenv("IBM_API_KEY")
crn = os.getenv("IBM_CRN")
if api_key and crn:
    QiskitRuntimeService.save_account(token=api_key, instance=crn, set_as_default=True)
else:
    print("IBM_API_KEY and IBM_CRN are not set")
