<script lang="ts">
  import { onMount } from "svelte";

  import "./tailwind.css";

  export let symptomInput = "";

  let symptoms = [];
  let mode: "original" | "check" = "original";
  let result = null;
  let symptomsFixedData: any = [];
  let includedChecks: string[] = [];

  const handleChangeSymptomInput = (e) => {
    symptomInput = e.target.value ?? "";
  };

  const handleAddSymptom = () => {
    symptoms = [...symptoms, symptomInput];
    symptomInput = "";
  };

  const handleRemoveSymptom = (i) => {
    symptoms = symptoms.filter((_, ix) => i !== ix);
  };

  const fetchSymptoms = async () => {
    try {
      const resp = await fetch(`${BASE_URL}/symptoms`);

      if (resp.status !== 200) throw await resp.text();

      return await resp.json();
    } catch (e) {
      return null;
    }
  };

  const handleFetchSymptoms = async () => {
    symptomsFixedData = await fetchSymptoms();
  };

  onMount(async () => {
    await Promise.all([handleFetchSymptoms()]);
  });

  const handleGetDiagnosis = async () => {
    try {
      const resp = await fetch(
        `${BASE_URL}/diagnose?input=${encodeURIComponent(
          JSON.stringify(symptoms)
        )}`
      );

      if (resp.status !== 200) throw await resp.text();

      result = await resp.json();
    } catch (e) {
      alert("Error diagnosis (original)");
      console.error(e);
    }
  };

  const handleDiagnoseCheck = async () => {
    try {
      const resp = await fetch(`${BASE_URL}/diagnose-by-check`, {
        method: "post",
        headers: {
          "content-type": "application/json",
        },
        body: JSON.stringify(includedChecks),
      });

      if (resp.status !== 200) throw await resp.text();

      result = await resp.json();
    } catch (e) {
      alert("Error diagnosis (check)");
      console.error(e);
    }
  };
</script>

<main>
  <div class="container mx-auto">
    <div class="flex justify-center flex-col items-center">
      <div class="text-xl font-bold flex justify-center">Dokkompi</div>
      <div class="italic">Search engine untuk diagnosa kerusakan PC</div>
    </div>
    <div class="border-2 my-2">
      <hr />
    </div>

    <div class="flex">
      <div>
        <button
          on:click={() => {
            mode = "original";
          }}
          class={`p-1 ${
            mode === "original"
              ? "bg-blue-500 text-white"
              : "bg-white text-black"
          }`}
          style="cursor:pointer"
        >
          Original Layout
        </button>
      </div>

      <div>
        <button
          on:click={() => {
            mode = "check";
          }}
          class={`p-1  ${
            mode === "check" ? "bg-blue-500 text-white" : "bg-white text-black"
          }`}
          style="cursor:pointer"
        >
          Checklist Layout
        </button>
      </div>
    </div>

    {#if mode === "original"}
      <div>
        <div>
          <div>
            Kasih tau beberapa gejala kerusakan PC anda, dan list kemungkinan
            hardware yang rusak akan muncul.
          </div>
          <div>Contoh:</div>
          <ol class="list-decimal text-gray-700 font-bold">
            <li>Muncul tulisan hard disk error failure</li>
            <li>Blue screen</li>
            <li>Boot ke safe mode</li>
          </ol>
        </div>
        <div class="my-2">
          <div class="flex">
            <input
              class="border border-gray-300 p-2"
              placeholder="Masukkan gejala di sini..."
              on:blur={handleChangeSymptomInput}
              value={symptomInput}
            />
            <button
              on:click={handleAddSymptom}
              class="mx-2 px-2 py-1 font-bold rounded-lg text-white bg-blue-500 hover:bg-blue-700"
              >Tambah</button
            >
          </div>
        </div>
        <ol class="list-decimal" />
        {#each symptoms as symptom, i}
          <li
            class="hover:text-red-600 cursor-pointer hover:underline"
            on:click={() => handleRemoveSymptom(i)}
          >
            {symptom}
          </li>
        {/each}
        {#if (symptoms?.length ?? 0) > 0}
          <div class="my-2 ">
            <button
              on:click={handleGetDiagnosis}
              class="px-2 py-1 font-bold rounded-lg text-white bg-green-500 hover:bg-green-700"
              >Diagnosa</button
            >
          </div>
        {/if}
      </div>
    {/if}

    {#if mode === "check"}
      <div
        class="container mx-auto overflow-auto resize-y"
        style="height: 75vh;"
      >
        <table class="w-full table-auto border-separate">
          <thead>
            <tr>
              <th
                class="border-solid border-2 border-gray-400 text-white sticky top-0 bg-gray-600"
                >#</th
              >
              <th
                class="border-solid border-2 border-gray-400 text-white sticky top-0 bg-gray-600"
                >Ada Gejala</th
              >
              <th
                class="border-solid border-2 border-gray-400 text-white sticky top-0 bg-gray-600"
                >Jenis Gejala</th
              >
            </tr>
          </thead>
          <!-- <small>
            <pre>
              {JSON.stringify(includedChecks, null, 2)}
            </pre>
          </small> -->
          <tbody>
            {#each symptomsFixedData?.symptoms ?? [] as s, i}
              <tr>
                <td class="border-solid border-2 border-gray-400 p-1">
                  {i + 1}
                </td>
                <td class="border-solid border-2 border-gray-400 p-1">
                  <div class="flex justify-center">
                    <input
                      type="checkbox"
                      on:change={(e) => {
                        if (includedChecks.find((sx) => sx === s?.name)) {
                          includedChecks = includedChecks.filter(
                            (sx) => sx !== s?.name
                          );
                        } else {
                          includedChecks = [...includedChecks, s?.name ?? ""];
                        }
                      }}
                    />
                  </div>
                </td>
                <td class="border-solid border-2 border-gray-400 p-1">
                  {s?.name}
                </td>
              </tr>
            {/each}
          </tbody>
        </table>
      </div>
      <div>
        {#if (includedChecks?.length ?? 0) > 0}
          <div class="my-2 ">
            <button
              on:click={handleDiagnoseCheck}
              class="px-2 py-1 font-bold rounded-lg text-white bg-green-500 hover:bg-green-700"
              >Diagnosa</button
            >
          </div>
        {/if}
      </div>
    {/if}

    {#if result}
      <div>
        <div class="text-xl text-blue-600 font-bold">Result</div>

        {#each result?.saw_result?.sort((a, b) => (b?.normalised_result ?? 0) - (a?.normalised_result ?? 0)) as saw}
          <div>
            {saw?.classification?.name}
            <strong>
              | {(
                ((saw?.normalised_result ?? 0) /
                  result?.saw_result?.reduce(
                    (acc, saw) => acc + (saw?.normalised_result ?? 0),
                    0
                  )) *
                100
              ).toFixed(2)} %</strong
            >
          </div>
        {/each}
      </div>
    {/if}
  </div>
</main>
