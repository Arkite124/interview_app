비교 축|OpenAI SDK (직접 루프)|Agents SDK (runtime 관리)|LCEL (chain 조립)
코드량|예시: 호출·재시도·상태 처리를 전부 내가 작성해야 해서 같은 기능 기준 코드가 가장 길어요.| 같은 기능에 SDK가 부분적으로 호출과 상태처리를 맡아서 비교적 쉽다.|LangChain 안에 처리해야 하는 것이 내장 되어있음
모델 교체 | 각 모듈 별로 모델 이름을 호출하는 곳에 명시적으로 바꿔 주기만 하면 사용 모델이 교체 됨/사용 agent 별로 이름이 다름 | LangChain은 init_chat_model의 "provider:model_name" 문자열만 바꾸면 chain 본문은 그대로예요.
도구/상태 | 전부 직접 작성 | 부분적으로 상태 작성 | 프롬포트만 작성하고 상태는 작성할 필요 없음
streaming | 비동기 호출로 데이터를 조각별로 날아오는걸 받아서 작성 프론트 엔드에 data, delta값을 빼고 전송 | SDK도 동일 | LangChain은 비동기 처리만 해주면 스트리밍은 내부적으로 처리되고 텍스트만 전송
RAG 확장성 | 힘듬 | 비교적 힘듬 | 원활 


“Step 1은 tool/state orchestration이 아니라 prompt-model-parser 이식이 목표라서 LCEL을 선택한다. 다양한 agent들에 따라 구조가 바뀌지 않는 획일성이 좋다.”




