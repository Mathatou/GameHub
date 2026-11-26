import {
  getGame,
  getRandomGame,
  removeGameFromLib,
  addGameToLib
} from "./api.js";

import {
  myNotification,
  lNotifications,
  addNotification,
  dismissNotification,
  mergeNotifications
} from "./notifications.js";

let nextNotificationId = 1; // Unique ID for each notification

const { createApp, ref, computed } = Vue;
function describeGame(g) {
  return `${g.name} (${g.min_players}-${g.max_players} players, ` +
         `${g.playing_time} min, complexity ${g.complexity.toFixed(1)})`;
}

function notify(content, kind, isSticky = false, {label = null, action = null } = {}) 
{
  const notification = new myNotification(nextNotificationId++, 
    content, 
    kind, 
    isSticky, 
    {label, action});
  addNotification(notification);
}


// Component: one game card with its button
const GameCard = {
  props: ["game", "inLibrary"],
  emits: ["add", "remove"],
  data() {
    return { added: false };
  },
  computed: {
    label() {
      return describeGame(this.game);
    },
  },
  methods: {
    onClick() {
      if (this.inLibrary) {
        this.$emit("remove", this.game.id);
      } else {
        this.$emit("add", this.game.id);
        this.added = true;
      }
    },
  },
  template: `
    <li>
      <span>{{ label }}</span>
      <button :disabled="added" @click="onClick">
        {{ inLibrary ? "Remove" : (added ? "Added ✓" : "Add to library") }}
      </button>
    </li>`,
};

createApp({
  components: { GameCard },
  setup() {
    // Interface state: when these change, the page updates by itself
    const players = ref("");
    const maxTime = ref("");
    const maxComplexity = ref("");
    const source = ref("catalog");

    const games = ref([]);
    const count = ref(null);
    const listSource = ref("catalog");   // source used for the displayed list
    const randomGame = ref(null);
    const noRandom = ref(false);

    const message = computed(() => {
      if (count.value === null) return "";
      const shown = games.value.length;
      return `${count.value} games found` +
             (count.value > shown ? ` (showing ${shown})` : "");
    });

    // Blank fields are simply not sent, so the backend ignores them
    function buildParams(usedSource) {
      const params = new URLSearchParams({ source: usedSource });
      const filled = (v) => v !== "" && v !== null;
      if (filled(players.value)) params.append("players", players.value);
      if (filled(maxTime.value)) params.append("max_time", maxTime.value);
      if (filled(maxComplexity.value)) params.append("max_complexity", maxComplexity.value);
      return params;
    }

    async function search() {
      const usedSource = source.value;
      randomGame.value = null;
      noRandom.value = false;
      const response = await fetch(`/games?${buildParams(usedSource)}`);
      const data = await response.json();
      games.value = data.games;
      count.value = data.count;
      listSource.value = usedSource;
    }

    async function pickRandom() {
      const response = await fetch(`/games/random?${buildParams(source.value)}`);
      if (!response.ok) {
        randomGame.value = null;
        noRandom.value = true;
        return;
      }
      randomGame.value = await response.json();
      noRandom.value = false;
    }

    async function addGame(id) {
      const receipt = await addGameToLib(id);
      if (!receipt.ok) {
        notify(
          // TODO Error message to upgrade : "Game Name" not found in lib
          `Failed to add game: ${receipt.error ?? "Unknown error"}`,
          "failure",
        );
        return;
      }
      notify("Game added successfully!", "success");
    }

    async function removeGame(id) {
      const receipt = await removeGameFromLib(id);
      if (!receipt.ok) {
        notify(
          // TODO Error message to upgrade : "Game Name" not found in lib 
          `Failed to remove game: ${receipt.error ?? "Unknown error"}`,
          "failure",
        );
        return;
      }
      games.value = games.value.filter((game) => game.id !== id);
      count.value -= 1;
      notify(`Game removed successfully!`, "success");
    }

    // async function search()
    // {
    //   randomGame.value = null;
    //   noRandom.value = false;
    //   const usedSource = source.value;
    //   const data = await getGame(buildParams(usedSource));
    //   games.value = data.games;
    //   count.value = data.count;
    //   listSource.value = usedSource;
    // }

    // async function pickRandom()
    // {
    //   const usedSource = source.value;
    //   const data = await getRandomGame(buildParams(usedSource));
    //   randomGame.value = data;
    //   noRandom.value = data === null;
    // }
    // async function removeGame(id) 
    // {
    //   await removeGameFromLib(id);
    //   games.value = games.value.filter(g => g.id !== id);
    //   count.value--;
    // }
    return {
      players, maxTime, maxComplexity, source,
      games, listSource, randomGame, noRandom, message,
      search, pickRandom, addGame, removeGame, describeGame,
      lNotifications, myNotification, addNotification, dismissNotification, mergeNotifications
    };
  },
}).mount("#app");